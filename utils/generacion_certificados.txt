openssl genrsa -out modbusPY.key -des 1024
openssl req -new -x509 -key modbusPY.key -out modbusPY.pem -outform pem -config E:\ModbusPY\openssl-0.9.8\share\openssl.cnf
openssl x509 -in modbusPY.pem -inform pem -out modbusPY.der -outform der


openssl req -x509 -newkey rsa:2048 -keyout my_private_key.pem -out my_cert.pem -days 355 -nodes -config E:\ModbusPY\openssl-0.9.8\share\openssl.cnf
openssl x509 -outform der -in my_cert.pem -out my_cert.der