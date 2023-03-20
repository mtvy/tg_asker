package database

import (
	"context"
	"errors"

	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/sirupsen/logrus"
)

var (
	ErrorNoConnections error = errors.New("Database is Disconnected!")

	ErrorToManyClients error = errors.New("FATAL: sorry, too many clients already (SQLSTATE 53300)")
	ErrorDbConnection  error = errors.New("Database Connecting Error!")
	ErrorRowsGetting   error = errors.New("Getting Rows From Database Error!")

	ErrorDbHostNotDefined error = errors.New("Database Host is not defined!")
	// ErrorDbParseConfing error = errors.New("Parse database config error!")
)

type Connector interface {
	Connect(ctx context.Context, log logrus.FieldLogger) error
	IsValid(ctx context.Context, log logrus.FieldLogger) error
	DisConnect(ctx context.Context, log logrus.FieldLogger) error
	SendReq(ctx context.Context, log logrus.FieldLogger, msg string, args ...any) (map[int][]interface{}, error)
}

type Database struct {
	Host string
	pool *pgxpool.Pool
}

func NewDb(host string) Connector {
	return &Database{Host: host}
}

func (db *Database) IsValid(ctx context.Context, log logrus.FieldLogger) error {
	if db.pool == nil {
		return ErrorNoConnections
	}
	return nil
}

func (db *Database) Connect(ctx context.Context, log logrus.FieldLogger) error {

	if db.Host == "" {
		return ErrorDbHostNotDefined
	}

	// config, err := pgconn.ParseConfig(db.Host)
	// if err != nil {
	// 	log.Error(err)
	// 	return ErrorDbParseConfing
	// }

	// conn, err := pgconn.ConnectConfig(context.Background(), config)
	// if err != nil {
	// 	panic(err)
	// }

	pool, err := pgxpool.Connect(context.Background(), db.Host)
	if err != nil {
		log.Errorf(err.Error())
		return ErrorDbConnection
	}
	log.Infof("Connection Added {%s}", db.Host)
	db.pool = pool

	return nil
}

func (db *Database) DisConnect(ctx context.Context, log logrus.FieldLogger) error {
	if err := db.IsValid(ctx, log); err != nil {
		return err
	}
	log.Infof("Disconnected {%s}", db.Host)
	db.pool.Close()
	return nil
}

func (db *Database) SendReq(ctx context.Context, log logrus.FieldLogger, msg string, args ...any) (map[int][]interface{}, error) {
	log.Infof("Request {%s}", msg)
	err := db.IsValid(ctx, log)
	if err != nil {
		return nil, err
	}

	rows, err := db.pool.Query(context.Background(), msg, args...)
	if err != nil {
		log.Errorf(err.Error())
		return nil, ErrorRowsGetting
	}
	log.Infof("Rows {%s}", rows)

	data := map[int][]interface{}{}
	counter := 0
	for ; rows.Next(); counter++ {
		data[counter], err = rows.Values()
		if err != nil {
			log.Errorf(err.Error())
			return data, err
		}
	}
	log.Infof("Data {%s}", data)

	return data, nil
}
