import socket

from loguru import logger

from device_drivers.scales.tenzo_m.utils import decode_response, generate_random_weight_response

HOST = '127.0.0.1'
PORT = 9999

MIN_WEIGHT = 0.0
MAX_WEIGHT = 2.0

# пример ответа с весом b'\xff\x01\xc3E \x0036\xff\xff'


def main() -> None:
    """Симулятор весов.

    Запуск python simulator.py
    Синхронный, так как здесь нет IO-bound операций.
    Запускается на указанном в HOST:PORT адресе.
    Вес генерируется как случайный в диапазоне от MIN_WEIGHT до MAX_WEIGHT.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        logger.info(f'🚀 Симулятор запущен на адресе {HOST}:{PORT}')

        # Цикл по подключениям разных клиентов
        while True:
            try:
                client_socket, addr = server_socket.accept()
                logger.info(f'⭐️  Установлено соединение с клиентом {addr}')

                with client_socket:
                    # Цикл по сообщениям одного клиента
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            logger.info('❌ Клиент закрыл соединение')
                            break

                        logger.info(f'⬅️  Получены данные: {data}')

                        response: bytes = generate_random_weight_response(MIN_WEIGHT, MAX_WEIGHT)
                        response_decoded: tuple | None = decode_response(response)

                        # Чтобы линтер не ругался, вряд ли мы сами сгенерируем неверный ответ
                        if response_decoded is None:
                            logger.error('❌ Сгенерированный ответ не соответствует протоколу')
                            break

                        weight, stable, overload = response_decoded

                        client_socket.sendall(response)
                        logger.info(f'➡️  Отправлены данные: weight={weight}, stable={stable}, overload={overload}')

            except ConnectionResetError:
                logger.warning('⚠️ Соединение было сброшено клиентом')
                continue
            except KeyboardInterrupt:
                logger.info('🛑 Симулятор остановлен вручную')
                break


if __name__ == '__main__':
    main()
