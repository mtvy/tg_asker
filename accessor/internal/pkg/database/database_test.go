package database

import (
	"context"
	"testing"

	"github.com/mtvy/grpc_database_accessor/internal/pkg/logger"

	"github.com/stretchr/testify/require"
)

const (
	TESTLOKILABEL    = "{source=\"database_test.go\",job=\"testing\"}"
	TESTERRLOKILABEL = "{source=\"database_test.go\",job=\"testing_errors\"}"
	TESTCONFIG       = "../../../config/config_test.yaml"
)

// "postgres://username:password@localhost:5432/database_name"
var (
	db  = NewDb("postgres://postgres:postgres@0.0.0.0:5432/postgres")
	log = logger.New()
	ctx = context.Background()
)

func TestDatabase(t *testing.T) {
	if err := db.Connect(ctx, log); err != nil {
		log.Errorf(err.Error())
	}
	defer func() {
		if err := db.DisConnect(ctx, log); err != nil {
			log.Errorf(err.Error())
		}
	}()

	t.Run("INSERT", func(t *testing.T) {
		order := NewInsertOrder("qrcodes_tb", "url, name", "('Hello', 'World')")
		_, err := db.SendReq(ctx, log, order.Msg)

		log.Warnf("[INSERT Return Value]")

		require.NoError(t, err)
	})
	t.Run("GET", func(t *testing.T) {
		order := NewGetOrder("qrcodes_tb", "*", "WHERE url='Hello'")
		_, err := db.SendReq(ctx, log, order.Msg)

		log.Warnf("[GET Return Value]")

		require.NoError(t, err)
	})
	t.Run("UPDATE", func(t *testing.T) {
		order := NewUpdateOrder("qrcodes_tb", "url='Bye'", "WHERE url='Hello'")
		_, err := db.SendReq(ctx, log, order.Msg)

		log.Warnf("[UPDATE Return Value]")

		require.NoError(t, err)
	})
	t.Run("DELETE", func(t *testing.T) {
		order := NewDeleteOrder("qrcodes_tb", "WHERE url='Hello'")
		_, err := db.SendReq(ctx, log, order.Msg)

		log.Warnf("[DELETE Return Value]")

		require.NoError(t, err)
	})
	t.Run("EMPTY_GET", func(t *testing.T) {
		order := NewGetOrder("qrcodes_tb", "*", "WHERE url='Hello'")
		_, err := db.SendReq(ctx, log, order.Msg)

		log.Warnf("[GET Return Value]")

		require.NoError(t, err)
	})
}

func TestDatabaseError(t *testing.T) {
	t.Run("Connection Error", func(t *testing.T) {
		errDb := NewDb("postgres://postgres:postgres@0.0.0.0:5434/postgres")
		order := NewGetOrder("*", "some_tb", "")
		_, err := errDb.SendReq(ctx, log, order.Msg)
		require.ErrorIs(t, err, ErrorNoConnections)
	})
	t.Run("Connection Error", func(t *testing.T) {
		errDb := NewDb("postgres://postgres:postgres@0.0.0.0:5434/postgres")
		err := errDb.DisConnect(ctx, log)
		require.ErrorIs(t, err, ErrorNoConnections)
	})
	t.Run("Connection Error", func(t *testing.T) {
		errDb := NewDb("postgres://postgres:postgres@0.0.0.0:5434/postgres")
		err := errDb.Connect(ctx, log)
		require.ErrorIs(t, err, ErrorDbConnection)
	})
	t.Run("Getting Error", func(t *testing.T) {
		errDb := NewDb("postgres://postgres:postgres@0.0.0.0:5432/postgres")
		if err := errDb.Connect(ctx, log); err != nil {
			log.Errorf(err.Error())
		}
		defer func() {
			if err := errDb.DisConnect(ctx, log); err != nil {
				require.NoError(t, err)
			}
		}()
		order := NewGetOrder("*", "some_tb", "")
		_, err := errDb.SendReq(ctx, log, order.Msg)
		require.ErrorIs(t, err, ErrorRowsGetting)
	})
}
