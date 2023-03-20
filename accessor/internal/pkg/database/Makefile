# - - - - - - - - - - - - - - - - -
# Testing tools
# - - - - - - - - - - - - - - - - -
cover:
	go test -short -count=1 -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out
	rm coverage.out

test:
	go test -run=.
# - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - -
# Benchmark
# - - - - - - - - - - - - - - - - -
bconn:
	GOGC=off go test -bench=BechmarkConnections ./ -cpuprofile conn_cpu.out
	go tool pprof --edgefraction=0 --nodefraction=0 --nodecount=100000 database.test conn_cpu.out
	rm database.test conn_cpu.out

binsert:
	GOGC=off go test -bench=BenchmarkInsert ./ -cpuprofile insert_cpu.out
	go tool pprof --edgefraction=0 --nodefraction=0 --nodecount=100000 database.test insert_cpu.out
	rm database.test insert_cpu.out

bdelete:
	GOGC=off go test -bench=BenchmarkDelete ./ -cpuprofile delete_cpu.out
	go tool pprof --edgefraction=0 --nodefraction=0 --nodecount=100000 database.test delete_cpu.out
	rm database.test delete_cpu.out
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Mock
# - - - - - - - - - - - - - - - - -
mock:
	mockgen -source=database.go -destination=mocks/mock_database.go
# - - - - - - - - - - - - - - - - -
