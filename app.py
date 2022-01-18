# from crypt import methods

from uuid import uuid4
from flask import jsonify 
from flask import request 
from flask import Flask

#import our blockchain
from block import Blockchain


#initiate flask node

app = Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = Blockchain()


@app.route('/mine',methods=['GET'])
def mine ():
    """
    # We run the proof of work algorithm to get the next proof...
    """
    
    last_block = blockchain.lastblock
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #if proof has been mined, for incoming transac give this node one coin 
    if proof :
        
        blockchain.newtransaction(
        sender="0",
        recipient=node_id,#signifies that node is getting paid for mining 
        amount=1,
        )

    #forge a new block to add to the chain 
    previous_hash = blockchain.hash(last_block)
    block = blockchain.newblock(proof, previous_hash)

    if block:
        
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return jsonify(response), 200
    response = {'message': 'failed at adding new blcok'}
    return jsonify('response'),404

@app.route('/transaction/new',methods=['POST']) 
def new_transaction ():
    """
    expected data : 
        {
        "sender": "my address",
        "recipient": "someone else's address",
        "amount": 5
        }
    
    """
    transaction = request.get_json()

    #validate incoming transaction 
    required = ['sender', 'recipient', 'amount']
    if not all(k in transaction for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.newtransaction(transaction['sender'], transaction['recipient'], transaction['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
