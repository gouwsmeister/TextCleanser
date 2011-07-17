RESOURCE: LEXICAL NORMALISATION ANNOTATIONS FOR TWEETS

VERSION: 1.0
LAST UPDATE: April 3rd, 2011

DESCRIPTION: 
This is the dataset used for lexical tweets normalisation described in:

Bo Han and Timothy Baldwin. Lexical normalisation of short text messages: Makn sens a #twitter. In The 49th Annual Meeting of the Association for Computational Linguistics, Portland, Oregon, USA, 2011.

It has 549 English tweets sampled from Twitter API (from August to October, 2010) and contains 1184 normalised tokens.
* The annotation targets one ill-formed word to one word correction (e.g. u -> you), it ignores one to many scenarios (e.g. ttyl -> talk to you later).
* Normalisations are always from Out-of-vocabulary words to In-vocabulary words relative to Aspell dictionary (version 0.60.6 with minor modification, see more in the paper), and context sensitive normalisation is out of current scope (e.g. wit -> with).
* Ill-formed words consist of letters, digits, and combinations with hyphen (-) and single quote ('). Hashtags, mentions and urls are reserved and untouched.
* Informal contractions are kept in their original forms (e.g. gonna, wanna).

Data format is:
<Num of tweets tokens>
<input 1>	<norm 1>
<input 2>	<norm 2>
......

meaning that each annotation begins with the token number of a tweet, followed by input tokens and normalised tokens separated by '\t'. If the input token is an ill-formed token, the normalisation part is given by the annotator, otherwise, input token is simply copied to the normalisation part. Here is an example,
4
new	new
pix	pictures
comming	coming
tomoroe	tomorrow

The above tweet has 4 tokens, the first token is same with its normalisation part, and last three tokens are ill-formed tokens with normalisations.

LICENSE:
This dataset is made available under the terms of the Creative Commons Attribution 3.0 Unported licence (http://creativecommons.org/licenses/by/3.0/), with attribution via citation of the following paper:

Bo Han and Timothy Baldwin. Lexical normalisation of short text messages: Makn sens a #twitter. In The 49th Annual Meeting of the Association for Computational Linguistics, Portland, Oregon, USA, 2011.

DISCLAIMER:
The dataset may contain offensive messages. They do not necessarily represent the views, policies or opinions of annotators and The University of Melbourne.
The dataset should be used appropriately in regard to legal and ethical issues.

ACKNOWLEDGEMENTS:
Many thanks to Marco Lui, Li Wang for their efforts in annotation.


CONTACTS:
The dataset is in the preliminary stage, and we are still trying to improve it. Any comments or suggestions are appreciated. 
Bo HAN (hanb@student.unimelb.edu.au)
Tim Baldwin (tb@ldwin.net)
