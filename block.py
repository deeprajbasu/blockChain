# from crypt import methods
from time import time
import json
import hashlib
from uuid import uuid4
from flask import jsonify 
from flask import request 
from flask import Flask

class blockchain (object):
    def __init__(self):
        self.chain = []

        #these blocks are to be added to the chain
        self.current_transactions = []

        #genesis block
        self.newblock(previoushash=1,proof = 100)


    def newblock(self,previoushash=None,proof=None):

        #construct block
        block = {
            'index':len(self.chain)+1,
            'timestamp':time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previoushash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block




    def newtransaction(self,sender, recipient, amount):
        """
        Create a new valid transaction to make block to go into block chain 

        params :-
        *sender: <str> Address of the Sender
        *recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof


        :param last_proof: <int>
        :return: <int>


        """

        proof = 0
        
        #method to compute valid proof
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        #current guess
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        #returns true when claclulation is done
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash for eacch block
        :param block: <dict> Block
        :return: <str>
        """

        #use ordered dict of each block as string to create the hash

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def lastblock(self):

        #return last block in chain
        self.chain[-1]

#initiate flask node

app = Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = blockchain()


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
