import asyncio


def print_task(task):
    print("Имя:", task.get_name())
    print("Готово:", task.done())
    print("Цикл:", task.get_loop())
    print("Корутина:", task.get_coro())

async def foo():
    task = asyncio.current_task().get_name()

    try:
        for i in range(10):
            print(f'foo {i} from task {task}')
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"Задача {task} отменена")
        raise


async def main():
    my_tasks = [asyncio.create_task(foo(), name=f'foo{i}') for i in range(1, 4)]

    try:
        await asyncio.gather(*my_tasks)
    except asyncio.CancelledError:
        print('Отмена внутри') 
        for task in my_tasks:
            print(f'Выполнена ли {task.get_name()}? {task.done()}')
            if not task.done():
                task.cancel()

        await asyncio.gather(*my_tasks, return_exceptions=True)
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Отмена снаружи')  