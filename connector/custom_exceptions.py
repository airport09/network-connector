class NetworkNotFound(Exception):
     def __init__(self,
                  network):
        message = f'{network} was not found.'
        super().__init__(message)
