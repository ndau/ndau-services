#!/bin/bash

if [ -z $2 ]; then
        echo "Usage: ./nnr-drand.sh <mainnet | testnet | devnet> <prevalidate | submit>"
        exit 0
fi

NET=$1
ACTION=$2
TXTYPE="NominateNodeReward"
NDAUTOOL="/home/ec2-user/ndau"
KEYTOOL="/home/ec2-user/keytool"
NNR_ADDR="ndnc57ygj3cpvez8hhgt4u4miyvnf7xfedycctxtmepa6arp"
PK="npvtayjadtcbiduadejgn7p5icfdnx53tr2pqswcsk3fc6qbw2mnd5t7aev7f3374cducdctqqpuxt5ifg9naxbgqq7ipenyix7pfnzm9r97n9qufj9sqtxaf47t"

DRAND_SERVERS="https://api.drand.sh https://api2.drand.sh https://api3.drand.sh https://drand.cloudflare.com"

# Try all servers until we get a response. But once we get a response we assume that
# that server will remain responsive for the rest of the script (another second or two.)

for DRAND in $DRAND_SERVERS; do
        ROUNDNUM=`curl -s $DRAND/public/latest | jq .round`
        if [ ! -z $ROUNDNUM ]
        then
                break
        fi
done

if [ -z $ROUNDNUM ]; then
        echo "All DRAND servers are unresponsive."
        exit 0
fi

# Round to a certain number (100) of drand rounds.

let ROUND=($ROUNDNUM/100)*100

RANDHEX=`curl -s $DRAND/public/$ROUND | jq .randomness | cut -c2-17`
RAND=$(( 0x$RANDHEX ))
echo "Random number is $RAND ($RANDHEX)" | tee -a /home/ec2-user/random.log

SHORTHEX=${RANDHEX:0:4}
SHORT=$(( 0x$SHORTHEX ))
echo "Short random number is $SHORT ($SHORTHEX)" | tee -a /home/ec2-user/random.log

for N in {0..0}; do
    SEQUENCE=$(( `curl -s https://$NET-$N.ndau.tech:3030/account/account/$NNR_ADDR | jq '.[].sequence'` + 1 ))
done

# $DRAND is left as a signed 64-bit number. The transaction expects a signed number but it's
# typecast to unsigned when passed to SelectByGoodness

read -d '' TX << EOF

{
  "random": $RAND,
  "sequence": $SEQUENCE,
  "signatures": []
}
EOF

echo "Transaction is:" | tee -a /home/ec2-user/random.log
echo `echo $TX | jq .` | tee -a /home/ec2-user/random.log

# Create a b64 encoded string of signable bytes to be signed externally

SIGNABLE_BYTES=$(echo $TX | $NDAUTOOL signable-bytes --hex "$TXTYPE")

# Sign bytes of TX with validation private key

SIGNATURE=$($KEYTOOL sign $PK "$SIGNABLE_BYTES" --hex)
SIGNED_TX=`echo $TX | sed -e s/\\\\[\\\\]/\\\\['"'$SIGNATURE'"'\]/`

echo $SIGNABLE_BYTES
echo $SIGNATURE
echo $SIGNED_TX

for N in {0..4}; do
    echo `curl -s -H "Content-Type: application/json" -d "$SIGNED_TX" https://$NET-$N.ndau.tech:3030/tx/$ACTION/$TXTYPE`
done

echo
