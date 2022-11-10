import requests
from lxml import html

for i in range(1, 401):
    urlblock = "https://etherscan.io/accounts" + str(i)
    respone_block = requests.get(urlblock)
    byte_string = respone_block.content
    source_code = html.fromstring(byte_string)
    xpatch_txid = '/html/body/main/div[3]/div/div/div[2]/table/tbody/tr[2]/td[2]'
    treetxid = source_code.xpath(xpatch_txid)
    ethVol = str(treetxid[0].text_content())
    ethVol = ethVol.split()[0]    

