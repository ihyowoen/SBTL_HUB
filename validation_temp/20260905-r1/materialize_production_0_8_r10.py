#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize_production_0_8.py')
text=SRC.read_text(encoding='utf-8')
repl={
'236b86f3a0cc7c0a862074884dc06303b0875a73337067e4d8e7a2f3d8e2ed86':'7b1c89c80b151306ddef5b67f7f239110c2f635d943d69adeab7426f7345de99',
'bafd91ebcbd5fcdc246c8fcc0ee1865d2489e77f94d9f1723f9da34a41f74bee':'cf7dac751f036821bdf8bc363e8d1fd02b4e65d0e38c639eaaf7114ce18ebbb2',
'c0407a7ab09cfdc501ef19f474598903a815d23e5a551566152f96efb96350f2':'efbe0aac7bce6bfad15d5629daa943b2cd1ec29beb5ceb062a66b93b8bb48d98',
'a1861b35f9865f2a4672e9d2ecc300d3a771d31d24ca2f319dc063a6cb76c961':'661917582f1ef0e1e1487507e2d3bc003ac1dc57f39a555bba10b8e7d660491f',
'6549427c4babdf94c38ff10a58bb9038fe46637e6b0c60d97c41e550bd2c6b33':'a90f92cb988948c91939a645b72ad0d654189bb64a24b2fe2c0185c22a1b2fb7',
'eccffdc19d1b2b9426896ccaf795189f38a37f4f2dfabc89f8c5c8bc15e7ba74':'905290f3998dc07a823c7975759c1221d2979315177425ca38ba8e1015f44ac1',
'e8c277544369405d6be14bafb14bec7f024b313145ef81de2bfb802f33fe809d':'ddfb3adfa8a08f8c8a9bef5bbe3c7d98f501c80853274bd36e803db7e6e1bef5',
'34a9f92858646da3b5d42d97011a772b2be0dba504f9dab12de22ee6ee57c8cb':'321580a42dc98c848984fbbb9b2114169408cc5dcafc3f5ecffcd189263faa0b',
'10013536223':'10015551124',
'4e8e4c4ab9c1f5be09320ef9c0901b796a186143b01ea9659a1a8a85dc9d97b3':'327cebb645625d7590365916c0452b025865d4b34037d52bb1c9a45156ee579e',
'34108930897':'34114132518',
}
for old,new in repl.items():
    assert old in text, old
    text=text.replace(old,new)
# Preserve and require the independent R10 nested binding instead of synthesizing stale data in 0.8.
needle="assert c07['hash_chain']==expected_hashes\n"
insert="assert c07['hash_chain']==expected_hashes\nassert c07['round_6_operation_binding']['stage_hashes']==expected_hashes\nassert c07['round_6_operation_binding']['reviewed_operations_sha256']==OPS_SHA\nassert c07['round_6_operation_binding']['binding_authority']=='independent_0_7c_r10_pre_0_8'\nassert c07['codex_p2_remediation']['status']=='PASS'\n"
assert needle in text
text=text.replace(needle,insert,1)
exec(compile(text,str(SRC)+'[R10_CERTIFIED_0_8]','exec'),{'__name__':'__main__','__file__':str(SRC)})
