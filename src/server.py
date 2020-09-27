import tornado.ioloop
import tornado.web
from json import loads, dumps
from dictionary import getDictionary
from crosswordmaker import CrossWordMaker

DICTIONARY = getDictionary('data/')

class CrossWordHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self):

        template = loads(self.request.body)        
        cwm = CrossWordMaker(template, DICTIONARY)
        completed = cwm.run()
        self.write(
            dumps(
                {
                    'clues': cwm.getClues(),
                    'board': cwm.board,
                    'completed': completed
                }
            )
        )

def make_app():
    return tornado.web.Application([(r"/", CrossWordHandler)])

if __name__ == "__main__":
    app = make_app()
    app.listen(8890)
    tornado.ioloop.IOLoop.current().start()