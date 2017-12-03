import os
import index
import json
import unittest
import tempfile

class EstropadakTestCase(unittest.TestCase):

    def setUp(self):
        self.app = index.app.test_client()
        #self.db_fd, index.app.config['DATABASE'] = tempfile.mkstemp()
        #index.app.config['TESTING'] = True
        #self.app = index.app.test_client()
        #with index.app.app_context():
        #    index.init_db()

    def tearDown(self):
        pass
        #os.close(self.db_fd)
        #os.unlink(index.app.config['DATABASE'])

    def testYears(self):
        rv = self.app.get('/years')
        years = json.loads(rv.data.decode('utf-8'))
        self.assertCountEqual(['act', 'arc1', 'arc2', 'euskotren'], years.keys())

    def testEstropadakList(self):
        rv = self.app.get('/estropadak/act/2010')
        estropadak = json.loads(rv.data.decode('utf-8'))
        print(estropadak)
        self.assertEqual(len(estropadak), 20)

    def testEstropadakListWithoutResults(self):
        rv = self.app.get('/estropadak/act/1900')
        estropadak = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(len(estropadak), 0)

    def testEstropadakListWithWrongLeague(self):
        rv = self.app.get('/estropadak/actt/2010')
        estropadak = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(len(estropadak), 0)

    def testEstropada(self):
        rv = self.app.get('/estropada/1c79d46b8c74ad399d54fd7ee40005e3')
        estropada = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(estropada['izena'], 'III Bandera Euskadi Basque Country')

    def testEstropadaNotFound(self):
        rv = self.app.get('/estropada/fuck')
        estropada = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(estropada, {} )

if __name__ == '__main__':
    unittest.main()
