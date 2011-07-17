package edu.isi.twitter_cleanser;

import org.apache.lucene.util.Attribute;

//import com.twitter.common.text.token.attribute.TokenType;

public interface CleanTokenAttribute extends Attribute, Cloneable {
	  
	void setCleanToken(CleanToken token);
	 
	CleanToken getCleanToken();
	
	Object clone();

}
