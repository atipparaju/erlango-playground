package main

import "testing"

func TestCounter(t *testing.T) {
 for _, cap := range []int{0, 16} {
  r, err := run(8, 250, cap)
  if err != nil { t.Fatal(err) }
  if r.Operations != 2000 { t.Fatalf("unexpected count: %d", r.Operations) }
 }
}
func TestInvalidInputs(t *testing.T) {
 if _, err := run(0, 1, 0); err == nil { t.Fatal("expected validation error") }
}
