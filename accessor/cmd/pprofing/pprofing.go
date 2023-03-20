package pprofing

import (
	"context"
	"net/http"

	"github.com/sirupsen/logrus"
)

func InitPprofing(ctx context.Context, log logrus.FieldLogger, host string) {
	log.Infof("Pprofing at {%s}", host)
	if err := http.ListenAndServe(host, nil); err != nil {
		log.Errorf(err.Error())
	}
}
