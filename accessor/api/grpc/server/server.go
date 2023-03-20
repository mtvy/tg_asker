package server

import (
	"context"
	"net"

	api "github.com/mtvy/grpc_database_accessor/api/grpc"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/database"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/logger"
	"github.com/mtvy/grpc_database_accessor/internal/pkg/utils"
	"github.com/sirupsen/logrus"
	tracesdk "go.opentelemetry.io/otel/sdk/trace"
	"google.golang.org/grpc"
)

// GRPCServer ...
type GRPCServer struct {
	api.UnimplementedDatabaseServer
	Db     database.Connector
	Tracer *tracesdk.TracerProvider
}

func ListenNServe(log logrus.FieldLogger, s *grpc.Server, host string) {
	l, err := net.Listen("tcp", host)
	if err != nil {
		log.Errorf(err.Error())
	}

	if err := s.Serve(l); err != nil {
		log.Fatal(err)
	}
}

func (server *GRPCServer) GetDb(ctx context.Context, req *api.GetDbRequest) (*api.GetDbResponse, error) {
	ctx, span := server.Tracer.Tracer("server").Start(ctx, "GetDb")
	defer span.End()

	order := database.NewGetOrder(req.Table, req.Columns, req.Condition)
	data, err := server.Db.SendReq(ctx, logger.New(), order.Msg)
	if err != nil {
		return &api.GetDbResponse{Status: err.Error(), Data: []byte{}}, nil
	}

	jsonData, err := utils.AnyToJson(data)
	if err != nil {
		return &api.GetDbResponse{Status: err.Error(), Data: []byte{}}, nil
	}

	return &api.GetDbResponse{Status: "ok", Data: jsonData}, nil
}

func (server *GRPCServer) InsertDb(ctx context.Context, req *api.InsertDbRequest) (*api.InsertDbResponse, error) {
	ctx, span := server.Tracer.Tracer("server").Start(ctx, "InsertDb")
	defer span.End()

	order := database.NewInsertOrder(req.Table, req.Columns, req.Values)
	_, err := server.Db.SendReq(ctx, logger.New(), order.Msg)
	if err != nil {
		return &api.InsertDbResponse{Status: err.Error()}, nil
	}
	return &api.InsertDbResponse{Status: "ok"}, nil
}

func (server *GRPCServer) DeleteDb(ctx context.Context, req *api.DeleteDbRequest) (*api.DeleteDbResponse, error) {
	ctx, span := server.Tracer.Tracer("server").Start(ctx, "DeleteDb")
	defer span.End()

	order := database.NewDeleteOrder(req.Table, req.Condition)
	_, err := server.Db.SendReq(ctx, logger.New(), order.Msg)
	if err != nil {
		return &api.DeleteDbResponse{Status: err.Error()}, nil
	}
	return &api.DeleteDbResponse{Status: "ok"}, nil
}

func (server *GRPCServer) UpdateDb(ctx context.Context, req *api.UpdateDbRequest) (*api.UpdateDbResponse, error) {
	ctx, span := server.Tracer.Tracer("server").Start(ctx, "UpdateDb")
	defer span.End()

	order := database.NewUpdateOrder(req.Table, req.ToSet, req.Condition)
	_, err := server.Db.SendReq(ctx, logger.New(), order.Msg)
	if err != nil {
		return &api.UpdateDbResponse{Status: err.Error()}, nil
	}
	return &api.UpdateDbResponse{Status: "ok"}, nil
}
