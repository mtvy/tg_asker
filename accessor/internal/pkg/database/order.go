package database

import (
	"context"

	"github.com/sirupsen/logrus"
)

type Requester interface {
	Get(ctx context.Context, log logrus.FieldLogger, db Connector) ([]interface{}, error)
	Insert(ctx context.Context, log logrus.FieldLogger, db Connector) ([]interface{}, error)
	Update(ctx context.Context, log logrus.FieldLogger, db Connector) ([]interface{}, error)
	Delete(ctx context.Context, log logrus.FieldLogger, db Connector) ([]interface{}, error)
}

type Order struct {
	Msg string
}

func NewOrder(msg string) *Order {
	return &Order{Msg: msg}
}

type GetOrder struct {
	*Order
}

func NewGetOrder(table, columns, condition string) *GetOrder {
	msg := "SELECT " + columns + " FROM " + table + " " + condition
	return &GetOrder{NewOrder(msg)}
}

type InsertOrder struct {
	*Order
}

func NewInsertOrder(table, columns, values string) *InsertOrder {
	msg := "INSERT INTO " + table + " (" + columns + ") VALUES " + values
	return &InsertOrder{NewOrder(msg)}
}

type UpdateOrder struct {
	*Order
}

func NewUpdateOrder(table, set, condition string) *UpdateOrder {
	msg := "UPDATE " + table + " SET " + set + " " + condition
	return &UpdateOrder{NewOrder(msg)}
}

type DeleteOrder struct {
	*Order
}

func NewDeleteOrder(table, condition string) *DeleteOrder {
	msg := "DELETE FROM " + table + " " + condition
	return &DeleteOrder{NewOrder(msg)}
}
