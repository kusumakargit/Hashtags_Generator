This repopsitory contains files, which are used in creation of Hashtags Generater web interface using hugging Face spaces.
Basically what the app file does is :
1) It loads a pre-trained model called "nlpconnect/vit-gpt2-image-captioning". a pre-trained model from hugging gace.
2) Whwn upploaded an image it passes it to the model and the model extracts features from image, thats nothing but edcoder part.
3) Next the festures are passed on the decoder model, which decodes them, to generate the context of the image.
4) Those multiple contexts are converted into hashtags, that is done by using extracting keywords using nltk.

web interface Link : https://kusumakar-hashtags-your-way.hf.space
Note : use it in incognito mode if in case the normal mode doesn't work in your browser - thats some unsolvable cache stuff in there. 
