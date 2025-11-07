from asyncio import open_connection, wait_for
import socket

from core.config import settings
from scales.base import BaseWeightClient

class TensoM(BaseWeightClient):
    '''
    Класс с реализацией протокола Тензо-М.
    Команды-запросы формируются как FF Adr COP CRC FF FF, всего 6 байт.
    Adr = Адрес, 1 байт, обычно 1
    COP = Код операции, 1 байт
    CRC = Контрольное значение, считается на основании Adr + CRC, для расчета есть метод
    Для используемых команд значения CRC заранее рассчитаны
    '''
    __get_gross_command =   b'\xFF\x01\xC3\xE3\xFF\xFF'
    __get_net_command =     b'\xFF\x01\xC2\x8A\xFF\xFF'
    __set_tare_command =    b'\xFF\x01\xC0\x58\xFF\xFF'
    __response_size_bytes = 100

    @staticmethod
    def _calculate_crc_with_null(data_bytes) -> str:
        '''Метод вычисления CRC согласно документации.
        Пример ввода данных: [0x01, 0xC0] (адрес и код операции)'''
        def crc_maker(b_input, b_crc):
            al = b_input
            ah = b_crc
            
            for _ in range(8):
                # rol al,1 - rotate AL left through carry
                # Save the carry from AL rotation
                carry_al = (al >> 7) & 1
                al = ((al << 1) & 0xFF) | carry_al
                
                # rcl ah,1 - rotate AH left through carry (using carry from AL)
                # Save the carry from AH rotation before modifying it
                carry_ah = (ah >> 7) & 1
                ah = ((ah << 1) & 0xFF) | carry_al
                
                # jnc mod2 - if no carry after rcl ah,1, skip XOR
                # The carry to check is the one from AH rotation (carry_ah)
                if carry_ah:
                    ah ^= 0x69
            
            return ah

        crc = 0x00
        
        # Process all data bytes
        for byte in data_bytes:
            crc = crc_maker(byte, crc)
        
        # Process null byte (0x00) at the end
        crc = crc_maker(0x00, crc)
        
        return f'{crc:02X}'

    @staticmethod
    def _decode_weight_frame(data: bytes) -> tuple:
        '''Разбираем полученный от весов поток. Возвращаем вес брутто, флаг стабильного веса и флаг перегруза.'''
        # Байты с весом
        W0, W1, W2, CON = data[3:7]

        # Декодируем BCD (обратный порядок байт)
        bcd_value = (W2 << 16) | (W1 << 8) | W0
        digits = f'{(bcd_value >> 16) & 0xFF:02X}{(bcd_value >> 8) & 0xFF:02X}{bcd_value & 0xFF:02X}'
        raw = int(digits)

        # Декодируем служебные данные CON
        sign = -1 if CON & 0b10000000 else 1
        decimal_pos = CON & 0b00000111
        stable = bool(CON & 0b00010000)
        overload = bool(CON & 0b00001000)

        weight = sign * (raw / (10 ** decimal_pos))
        return weight, stable, overload

    def __send_command(self, host: str, port: int, command: bytes) -> dict:
        '''(Устаревший) Метод синхронного взаимодействия с весами.'''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: 
                s.connect((host, port))
                s.settimeout(settings.GET_WEIGHT_TIMEOUT)

                s.sendall(command)
                response = s.recv(self.__response_size_bytes)
                return {'data': response}
            except KeyboardInterrupt:
                return {'error': 'Keyboard Interrupt'}
            except TimeoutError:
                return {'error': 'Timed Out'}
            except Exception as e:
                return {'error': e}

    async def send_command(self, host: str, port: int, command: bytes) -> dict:
        '''Метод асинхронного взаимодействия с весами.'''
        try:
            # Устанавливаем соединение по TCP, отправляем запрос
            reader, writer = await wait_for(open_connection(host, port), timeout=settings.GET_WEIGHT_TIMEOUT)
            writer.write(command)
            await writer.drain()

            # Получаем ответ
            response = await wait_for(reader.read(self.__response_size_bytes), timeout=settings.GET_WEIGHT_TIMEOUT)

            # Закрываем соединение
            writer.close()
            await wait_for(writer.wait_closed(), timeout=settings.GET_WEIGHT_TIMEOUT)

            return {'data': response}
        except Exception as e:
            return {'error': e}

    async def set_tare(self, host: str, port: int) -> dict:
        '''Устанавливаем текущую тару в ноль.'''
        await self.send_command(host, port, self.__set_tare_command)
        # Ответ не разбираем
        return {'OK': True}

    async def get_gross_weight(self, host: str, port: int) -> dict:
        '''Получаем вес брутто с весов.'''
        response: dict = await self.send_command(host, port, self.__get_gross_command)

        if 'error' in response.keys():
            return response

        weight, stable, overload = self._decode_weight_frame(response['data'])
        return {'gross': weight, 'stable_flag': stable, 'overload_flag': overload}

    async def get_net_weight(self, host: str, port: int) -> dict:
        '''Получаем вес нетто с весов.'''
        response: dict = await self.send_command(host, port, self.__get_net_command)

        if 'error' in response.keys():
            return response

        weight, stable, overload = self._decode_weight_frame(response['data'])
        return {'gross': weight, 'stable_flag': stable, 'overload_flag': overload}

