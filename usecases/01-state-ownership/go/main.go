package main

import (
 "encoding/json"
 "flag"
 "fmt"
 "os"
 "sync"
 "time"
)

type request struct { reply chan struct{} }

// counterActor is the sole owner of count. Each operation is synchronous,
// so mailbox depth reflects pending operations, not fire-and-forget traffic.
func counterActor(mailbox <-chan request, finished chan<- int64) {
 var count int64
 for req := range mailbox {
  count++
  req.reply <- struct{}{}
 }
 finished <- count
}

type result struct {
 Language string `json:"language"`
 Clients int `json:"clients"`
 OpsPerClient int `json:"ops_per_client"`
 Operations int64 `json:"operations"`
 ElapsedMS float64 `json:"elapsed_ms"`
 OpsPerSecond float64 `json:"ops_per_second"`
 MailboxCapacity int `json:"mailbox_capacity"`
}

func run(clients, ops, capacity int) (result, error) {
 if clients <= 0 || ops <= 0 || capacity < 0 {
  return result{}, fmt.Errorf("clients and ops must be positive; mailbox capacity must be non-negative")
 }
 mailbox := make(chan request, capacity)
 finished := make(chan int64, 1)
 go counterActor(mailbox, finished)
 start := time.Now()
 var wg sync.WaitGroup
 for i := 0; i < clients; i++ {
  wg.Add(1)
  go func() {
   defer wg.Done()
   reply := make(chan struct{})
   for j := 0; j < ops; j++ {
    mailbox <- request{reply: reply}
    <-reply
   }
  }()
 }
 wg.Wait()
 elapsed := time.Since(start)
 close(mailbox)
 count := <-finished
 expected := int64(clients) * int64(ops)
 if count != expected { return result{}, fmt.Errorf("counter mismatch: got %d, expected %d", count, expected) }
 seconds := elapsed.Seconds()
 return result{Language:"go", Clients:clients, OpsPerClient:ops, Operations:count,
  ElapsedMS:float64(elapsed.Microseconds())/1000, OpsPerSecond:float64(count)/seconds,
  MailboxCapacity:capacity}, nil
}

func main() {
 clients := flag.Int("clients", 4, "number of concurrent clients")
 ops := flag.Int("ops", 10000, "synchronous increments per client")
 capacity := flag.Int("mailbox", 0, "channel buffer capacity (0 = unbuffered)")
 flag.Parse()
 r, err := run(*clients, *ops, *capacity)
 if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(2) }
 if err := json.NewEncoder(os.Stdout).Encode(r); err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
}
