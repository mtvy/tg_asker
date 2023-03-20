# Golang Database Server processing

## Client modules
- <a href="https://github.com/mtvy/grpc_java_database_accessing"> Java Client (old)</a>
- <a href="https://github.com/mtvy/grpc_py_database_accessing"> Python Client (old)</a>

## Usage
```bash
make build # Build proto, linux main binary
```
```bash
make db # Start Database, Grafana, Loki, Jaeger
make up # Start Accessor, Prometheus
```
```bash
make shutdown # Down All
```
```bash
make shut # Down Only Accessor
```

## Testing tools
```bash
make cover # Check coverage
make test # Run testing, linters (golangci)
```

## Issue
```bash
go get -u google.golang.org/protobuf/cmd/protoc-gen-go
go install google.golang.org/protobuf/cmd/protoc-gen-go

go get -u google.golang.org/grpc/cmd/protoc-gen-go-grpc
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc
```
