from typing import BinaryIO

class NonCloseableFile:
    """
    Wrapper para um objeto de arquivo que impede que o método close() feche o arquivo real.
    Útil quando passamos o arquivo para bibliotecas que tentam fechá-lo (como pandas.read_csv em alguns casos),
    mas precisamos usar o arquivo novamente depois.
    """
    def __init__(self, file_obj: BinaryIO):
        self.file_obj = file_obj

    def __getattr__(self, name):
        return getattr(self.file_obj, name)

    def close(self):
        # Não faz nada
        pass
