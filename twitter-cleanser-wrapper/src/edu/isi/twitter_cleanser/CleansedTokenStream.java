package edu.isi.twitter_cleanser;

import java.nio.CharBuffer;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import com.twitter.common.text.token.TokenStream;
import com.twitter.common.text.token.TokenizedCharSequence;
import com.twitter.common.text.token.TokenizedCharSequence.Builder;
import com.twitter.common.text.token.TokenizedCharSequence.Token;
import com.twitter.common.text.token.attribute.CharSequenceTermAttribute;
import com.twitter.common.text.token.attribute.PartOfSpeechAttribute;
import com.twitter.common.text.token.attribute.TokenType;
import com.twitter.common.text.token.attribute.TokenTypeAttribute;

public class CleansedTokenStream extends TokenStream {
	private final CleanTokenAttribute ctAttribute;

//	private String[] tokens;
	private CleanToken[] cleanTokens;
	private int currIndex;
	private TextCleanserWrapper cleanser;

	public CleansedTokenStream() {
		this.ctAttribute = addAttribute(CleanTokenAttribute.class);
		this.cleanser = new TextCleanserWrapper();
	}

	@Override
	public boolean incrementToken() {
		if(this.currIndex == this.cleanTokens.length) {
			return false;
		}
		this.ctAttribute.setCleanToken(this.cleanTokens[this.currIndex]);
		this.currIndex++;
		return true;
	}
	
	@Override
	public void reset(CharSequence input) {
		String[] tagged = this.cleanser.cleanseTweet(input.toString()).split(" ");
//		this.tokens = new String[tagged.length];
		this.cleanTokens = new CleanToken[tagged.length];
		
		for(int i=0; i<tagged.length; i++) {
			cleanTokens[i] = new CleanToken(tagged[i]);
		}
		
		this.currIndex=0;
	}
}
