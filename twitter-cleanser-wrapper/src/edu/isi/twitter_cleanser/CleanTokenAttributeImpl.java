package edu.isi.twitter_cleanser;

import org.apache.lucene.util.AttributeImpl;
//import java.io.Serializable;

public class CleanTokenAttributeImpl extends AttributeImpl implements CleanTokenAttribute {

	private static final long serialVersionUID = 1L;
	
	private CleanToken token = null;

	// constructor
	public CleanTokenAttributeImpl() {
		
	}
	
	public CleanTokenAttributeImpl(CleanToken c) {
		token=c;		
	}
	
	@Override
	public void copyTo(AttributeImpl target) {
		if (target instanceof CleanTokenAttributeImpl) {
		      ((CleanTokenAttributeImpl) target).setCleanToken(getCleanToken());
		    }
	}

	@Override
	public boolean equals(Object other) {
		return other != null
        && other instanceof CleanTokenAttributeImpl
        && ((CleanTokenAttributeImpl) other).getCleanToken() == this.token;
	}

	@Override
	public int hashCode() {
		return token.hashCode();
	}

	@Override
	public Object clone() {
		CleanTokenAttribute result = (CleanTokenAttribute)super.clone();
		return result;
	}

	@Override
	public void clear() {
		token=null;
	}
	
	public void setCleanToken(CleanToken token){
		this.token = token;
	}
	
	public CleanToken getCleanToken() {
		return this.token;
	}


}
