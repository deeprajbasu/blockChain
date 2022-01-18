from time import time
import json
import hashlib

class Blockchain (object):
    def __init__(self):
        self.chain = []

        #these blocks are to be added to the chain
        self.current_transactions = []

        #genesis block
        self.newblock(previoushash=1,proof = 100)  

    @property
    def lastblock(self):

        #return last block in chain
        return self.chain[-1]


    def newblock(self,previoushash=None,proof=None):

        #construct block
        block = {
            'index':len(self.chain)+1,
            'timestamp':time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previoushash,
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

        return self.lastblock['index'] + 1

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


