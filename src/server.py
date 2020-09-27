import tornado.ioloop
import tornado.web
import tornado.gen
from json import loads, dumps
from dictionary import getDictionary
from crosswordmaker import CrossWordMaker
from concurrent.futures import ThreadPoolExecutor
import asyncio

DICTIONARY = getDictionary('../data')


class CrossWordHandler(tornado.web.RequestHandler):

    def initialize(self, pool):
        self.pool = pool

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    async def post(self):
        template = loads(self.request.body)
        cwm = CrossWordMaker(template, DICTIONARY)
        completed = await cwm.run()
        output = {
            'clues': cwm.getClues() if cwm else [],
            'board': cwm.board if cwm else [],
            'completed': completed
        }
        self.write(dumps(output))

def make_app():
    return tornado.web.Application([(r"/", CrossWordHandler, dict(pool=ThreadPoolExecutor()))])

if __name__ == "__main__":
    app = make_app()
    app.listen(8890)
    tornado.ioloop.IOLoop.current().start()