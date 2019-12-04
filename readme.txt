Utilizada a versão 3.5 do V-Rep Pro Edu e python 3

Instalar as bibliotecas:
sklearn:
pip install -U scikit-learn

pandas:
pip install pandas

Para executar, primeiramente abrir o V-Rep e carregar a cena KJunior.ttt
para a rede neural, rodar o arquivo KJuniorNN.py
em seguida começar a simulação no V-Rep

**Os arquivos remoteApi (.dll para windows e .so para linux) devem ser compatíveis com a sua versão do python
    nesse caso, foi utilizado o python 3 64 bits, se estiver com a versão 32 bits, substitua este arquivo por
    o que se encontra em "V-REP_PRO_EDU\programming\remoteApiBindings\lib\lib\*seu sistema operacional*\32Bit".