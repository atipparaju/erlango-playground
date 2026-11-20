-module(counter_bench).
-behaviour(gen_server).
-export([main/0, start_link/0, increment/1, get_count/1]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

%% One gen_server process owns all mutable counter state.
start_link() -> gen_server:start_link(?MODULE, [], []).
increment(Pid) -> gen_server:call(Pid, increment, infinity).
get_count(Pid) -> gen_server:call(Pid, get_count, infinity).

init([]) -> {ok, 0}.
handle_call(increment, _From, Count) -> {reply, ok, Count + 1};
handle_call(get_count, _From, Count) -> {reply, Count, Count}.
handle_cast(_Message, State) -> {noreply, State}.
handle_info(_Message, State) -> {noreply, State}.
terminate(_Reason, _State) -> ok.
code_change(_OldVersion, State, _Extra) -> {ok, State}.

main() ->
    try
        Args = init:get_plain_arguments(),
        {Clients, Ops} = parse_args(Args),
        {ok, Pid} = start_link(),
        Parent = self(),
        Start = erlang:monotonic_time(microsecond),
        [spawn_link(fun() -> repeat(Ops, fun() -> increment(Pid) end),
                             Parent ! {done, self()} end)
         || _ <- lists:seq(1, Clients)],
        wait_clients(Clients),
        Elapsed = erlang:monotonic_time(microsecond) - Start,
        Count = get_count(Pid),
        Expected = Clients * Ops,
        true = (Count =:= Expected),
        ok = gen_server:stop(Pid),
        Seconds = max(Elapsed / 1000000, 0.000001),
        io:format("{\"language\":\"erlang\",\"clients\":~B,\"ops_per_client\":~B,\"operations\":~B,\"elapsed_ms\":~.3f,\"ops_per_second\":~.3f,\"mailbox_capacity\":null}~n",
                  [Clients, Ops, Count, Elapsed / 1000, Count / Seconds]),
        halt(0)
    catch Class:Reason:Stack ->
        io:format(standard_error, "benchmark failed: ~p:~p ~p~n", [Class, Reason, Stack]),
        halt(2)
    end.

parse_args([C, O]) ->
    Clients = list_to_integer(C),
    Ops = list_to_integer(O),
    true = Clients > 0,
    true = Ops > 0,
    {Clients, Ops};
parse_args(_) -> erlang:error("expected two arguments: CLIENTS OPS").

repeat(0, _) -> ok;
repeat(N, Fun) -> Fun(), repeat(N - 1, Fun).

wait_clients(0) -> ok;
wait_clients(N) ->
    receive {done, _Pid} -> wait_clients(N - 1)
    after 120000 -> erlang:error(client_timeout)
    end.
