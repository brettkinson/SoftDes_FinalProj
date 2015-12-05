from pattern.en import sentiment
import indicoio
indicoio.config.api_key = 'f40bb2f1a1746e98919452261d38003a'

sen = 'Today is a good day!'

indi_1 = indicoio.sentiment(sen)
patt_1 = sentiment(sen)

print indi_1
print patt_1