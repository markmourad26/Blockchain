import datetime
import time
import hashlib
import json
import random
from flask import Flask, jsonify
 
 
class Blockchain:
   
    # create first block and set it's hash to "0"
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
        self.n = 5
        self.totaltime = 0
    
    def inc(self):
        self.n+=1
    def dec(self):
        if self.n > 1:
            self.n-=1
    def get_n(self):
        return self.n
    def get_add_total_time(self, t2):
        self.totaltime += t2
        return self.totaltime

    # creating blocks
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transaction': [random.randrange(1, 100, 1) for i in range(random.randrange(1, 10, 1))],
                 }
        self.chain.append(block)
        return block
    #if attackers creates blocks
    def create_block_attack(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transaction': "Attaaaaaaaacker"}
        self.chain.append(block)
        return block
       
    # display the previous block
    def print_previous_block(self):
        return self.chain[-1]
       
    # used to successfully mine the block
    def proof(self, previous_proof):
        new_proof = 1
        check_proof = False
         
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:self.n] == '0'*self.n:
                check_proof = True
            else:
                new_proof += 1
                 
        return new_proof
    
    
 
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
 
 
 

# Web App using flask
app = Flask(__name__)


blockchain = Blockchain()
 
# continues Mining new blocks
@app.route('/mine_block', methods=['GET'])
def mine_block():
    t1 = time.time()
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
     
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    t2 = time.time() - t1
    avgtime = blockchain.get_add_total_time(t2)/block['index']
    if avgtime > 1:
        blockchain.dec()
    else:
        blockchain.inc()
    print(t2)
    print(blockchain.get_n())
     
    return '''<meta http-equiv="refresh" content="0">{}
            '''.format(response)

# simulate 51% attack
@app.route('/51_attack/<x>', methods=['GET'])
def attack_51(x):
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    
    new_proof = 1
    new_proof_attack = 1
        
    while True:
        for i in range(100 - int(x)):
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '0'*5:
                previous_hash = blockchain.hash(previous_block)
                block = blockchain.create_block(new_proof, previous_hash)
                response = {'message': 'A block is MINED',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash'],
                    'transaction': block['transaction']}
                return jsonify(response), 200
            else:
                new_proof += 1

        for j in range(int(x)):
            hash_operation = hashlib.sha256(
                str(new_proof_attack**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '0'*5:
                previous_hash = blockchain.hash(previous_block)
                block = blockchain.create_block_attack(new_proof_attack, previous_hash)
                response = {'message': 'A block is MINED',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash'],
                    'transaction': block['transaction']}
                return jsonify(response), 200
            else:
                new_proof_attack += 1
        
 
# Display the whole blockchain
@app.route('/get_chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

 
 
# Run the flask server locally
app.run(host='127.0.0.1', port=1234)