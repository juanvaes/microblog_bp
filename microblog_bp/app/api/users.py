from . import api

@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    pass

@api.route('/users', methods=['GET'])
def get_users():
    pass

@api.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    pass

@api.route('/users/<int:id>/followed', methods=['GET'])
def get_followed(id):
    pass

@api.route('/users', methods=['POST'])
def create_user():
    pass

@api.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass