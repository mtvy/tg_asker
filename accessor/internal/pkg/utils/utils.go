package utils

import (
	"encoding/json"

	"github.com/sirupsen/logrus"
)

func AnyToJson(data interface{}) ([]byte, error) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		logrus.Println("Error while converting to JSON: ", err)
		return nil, err
	}

	return jsonData, nil
}
