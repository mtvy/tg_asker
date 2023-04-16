
# - - - - - - - - - - - - - - - - -
# Run Server
# - - - - - - - - - - - - - - - - -
run:
	go run cmd/main.go --conf=config/config.yaml
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Run Server
# - - - - - - - - - - - - - - - - -
db:
	cd deployments && sudo docker-compose -f docker-compose-database.yml up --build
db-d:
	cd deployments && sudo docker-compose -f docker-compose-database.yml up -d --build
db-down:
	cd deployments && sudo docker-compose -f docker-compose-database.yml down

up:
	cd deployments && sudo docker-compose up --build
up-d:
	cd deployments && sudo docker-compose up -d --build
down:
	cd deployments && sudo docker-compose down
shut:
	sudo docker stop postgres
	sudo docker stop db_exporter
	sudo docker stop grafana
	sudo docker stop loki
	sudo docker stop promtail
	sudo docker stop jaeger
	sudo docker stop prometheus
	sudo docker stop metrics_exporter
	sudo docker stop db_accessor
shutdown:
	cd deployments && sudo docker-compose -f docker-compose-database.yml down && sudo docker-compose down
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Building
# - - - - - - - - - - - - - - - - -
build: proto linux db

proto:
	protoc -I ./api/proto --go_out=. --go-grpc_out=. ./api/proto/database.proto

linux:
	GOOS=linux CGO_ENABLED=0 go build -o ./build/package/main ./cmd/main.go

local:
	go build -o ./build/package/main ./cmd/main.go
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Pprofing Server
# - - - - - - - - - - - - - - - - -
pprof:
	go tool pprof http://localhost:8024/debug/pprof/profile\?seconds\=10
pprof_trace:
	curl http://localhost:8024/debug/pprof/trace\?seconds\=10 > build/trace.out
	go tool trace build/trace.out
pprof_result:
	go tool pprof -http=localhost:8025 ./build/package/main /Users/mtvy/pprof/pprof.main.samples.cpu.002.pb.gz
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Push commit to git repo
# - - - - - - - - - - - - - - - - -
git:
	git add .
	git commit -m "$(COMMIT)"
	git push
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Database
# - - - - - - - - - - - - - - - - -
db_init:
	/Library/PostgreSQL/15/bin/psql -h 0.0.0.0 -p 5432 -U postgres -d postgres < deployments/database/init.sql
# - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - -
# Testing tools
# - - - - - - - - - - - - - - - - -
cover:
	go test -short -count=1 -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out
	rm coverage.out

test:
	go clean -testcache
	go test -run= ./internal/...
	golangci-lint run ./...
test_run: test
	go run cmd/main.go --conf=config/config_test.yaml
# - - - - - - - - - - - - - - - - -
