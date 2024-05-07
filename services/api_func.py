import asyncio
import dataclasses
import json
from pprint import pprint

import aiohttp

from config.bot_settings import logger
from database.db import ProfResult


async def get_prof(profession, salary, city, count=5):
    url = f"https://api.test.profdepo.ru/api/Aggregator/tgWorks?take={count}&skip=0"
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json-patch+json'
    }
    payload = json.dumps({
        "profession": f'{profession}',
        "salary": f'{salary}',
        "city": f'{city}'
    }, ensure_ascii=False)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            logger.debug(response.status)
            if response.status == 200:
                result = await response.json(encoding='UTF-8')
                return result
            else:
                raise ConnectionError(f'Неверный ответ от сервера: {response.status}')


async def get_result(profession, salary, city, count=5) -> list[ProfResult]:
    logger.debug(f'Запрос: {profession, salary, city, count}')
    json_results = await get_prof(profession=profession, salary=salary, city=city, count=count)
    # pprint(json_results)
    results = []
    for json_result in json_results:
        prof_result = ProfResult(
            id=json_result.get('id'),
            title=json_result.get('title'),
            city=json_result.get('city'),
            link=json_result.get('profdepoLink'),
            salary=json_result.get('compensationTo') or json_result.get('compensationFrom'),
        )
        results.append(prof_result)
    return results


async def main():
    profession = "разраб"
    salary = "10000"
    city = "Тюмень"
    json_results = await get_prof(profession=profession, salary=salary, city=city, count=5)
    pprint(json_results)


if __name__ == '__main__':
    asyncio.run(main())
