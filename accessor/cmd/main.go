package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"runtime"
	"syscall"
	"time"

	api "github.com/mtvy/grpc_database_accessor/api/grpc"
	"github.com/mtvy/grpc_database_accessor/api/grpc/server"
	"github.com/mtvy/grpc_database_accessor/cmd/config"
	"github.com/mtvy/grpc_database_accessor/cmd/pprofing"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/database"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/logger"
	metrics "github.com/mtvy/grpc_database_accessor/internal/pkg/metrics"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/trace"
	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/otel"
	tracesdk "go.opentelemetry.io/otel/sdk/trace"

	"google.golang.org/grpc"

	_ "net/http/pprof"
)

func main() {
	time.Sleep(5 * time.Second)
	runtime.SetBlockProfileRate(1)

	log := logger.New() // Get logger interface.
	ctx := context.Background()

	confFlag := flag.String("conf", "", "config yaml file")
	flag.Parse()

	confString := *confFlag
	if confString == "" {
		log.Fatal(" 'conf' flag required")
	}
	conf, err := config.Parse(confString)
	if err != nil {
		log.Fatalf("Conf Parse Error: %s", err)
	}

	gracefulShutdown := make(chan os.Signal, 1)
	signal.Notify(gracefulShutdown, syscall.SIGINT, syscall.SIGTERM)

	go metrics.InitPrometheus(ctx, log, conf.Prometheus)
	go pprofing.InitPprofing(ctx, log, conf.PprofPort)

	log.Infof("Starting the service at {%s}", conf.AppPort)

	db := database.NewDb(conf.DbHost)
	if err := db.Connect(ctx, log); err != nil {
		log.Errorf(err.Error())
	}

	// Tracer
	tp, err := trace.NewProvider("http://jaeger:14268/api/traces")
	if err != nil {
		log.Fatal(err)
	}
	// Register our TracerProvider as the global so any imported
	// instrumentation in the future will default to using it.
	otel.SetTracerProvider(tp)

	s := grpc.NewServer()
	srv := &server.GRPCServer{Db: db, Tracer: tp}
	api.RegisterDatabaseServer(s, srv)

	go server.ListenNServe(log, s, conf.AppPort)

	<-gracefulShutdown

	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer handleTermination(ctx, cancel, log, db, tp)
}

func handleTermination(ctx context.Context, cancel context.CancelFunc,
	log logrus.FieldLogger, db database.Connector, tp *tracesdk.TracerProvider) {
	defer log.Warnf("Not Really Graceful Shutdown.")
	defer func() {
		if err := db.DisConnect(ctx, log); err != nil {
			log.Errorf(err.Error())
		}
	}()
	defer tp.Shutdown(ctx)
	cancel()
}
