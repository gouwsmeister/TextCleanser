package edu.isi.twitter_cleanser;

import java.util.Iterator;
import java.util.List;

import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;
import org.apache.lucene.util.Attribute;

import com.twitter.common.text.token.TokenStream;
import com.twitter.common.text.token.TokenizedCharSequence;
import com.twitter.common.text.token.TokenizedCharSequence.Token;
import com.twitter.common.text.token.attribute.CharSequenceTermAttribute;
import com.twitter.common.text.token.attribute.TokenTypeAttribute;

import edu.isi.twitter_cleanser.CleanToken;
import edu.isi.twitter_cleanser.IsiTextCleanser;

/**
 * Annotated example illustrating major features of {@link DefaultTextTokenizer}.
 */
public class TextCleanserUsageExample {
  private static final String[] noisyFamousTweets = {
      // http://twitter.com/#!/BarackObama/status/992176676
      "W jus made history. All f dis happnd bcause u gave ur time, talent n passion."
        + "All of this happnd bcause of u. Thanks",
      // http://twitter.com/#!/jkrums/status/1121915133
      "http://twitpic.com/135xa - Thers a plane n da Hudson."
        + " Im n the ferri goin 2 pick up the ppl. Crazy.",
      // http://twitter.com/#!/carlbildt/status/73498110629904384
      "@khalidalkhalifa Tryin t get in tuch w u on an issue.",
  };

  public static void main(String[] args) {
    // This is the canonical way to create a token stream.
	  IsiTextCleanser tokenizer =
        new IsiTextCleanser.Builder().setKeepPunctuation(true).build();
	TokenStream stream = tokenizer.getDefaultTokenStream();

    // We're going to ask the token stream what type of attributes it makes available. "Attributes"
    // can be understood as "annotations" on the original text.
    System.out.println("Attributes available:");
    Iterator<Class<? extends Attribute>> iter = stream.getAttributeClassesIterator();
    while (iter.hasNext()) {
      Class<? extends Attribute> c = iter.next();
      System.out.println(" - " + c.getCanonicalName());
    }
    System.out.println("");

    // We're now going to iterate through a few tweets and tokenize each in turn.
    for (String tweet : noisyFamousTweets) {
      // We're first going to demonstrate the "token-by-token" method of consuming tweets.
      System.out.println("Processing: " + tweet);
      // Reset the token stream to process new input.
      stream.reset(tweet);

      // Now we're going to consume tokens from the stream.
      int tokenCnt = 0;
      while (stream.incrementToken()) {
        CleanTokenAttribute ctAttribute = stream.getAttribute(CleanTokenAttribute.class);
        System.out.println(String.format("%s", ctAttribute.getCleanToken().getToken()));
        tokenCnt++;
      }
      System.out.println("");

      // We're now going to demonstrate the TokenizedCharSequence API.
      // This should produce exactly the same result as above.
      tokenCnt = 0;
      System.out.println("Processing: " + tweet);
      List<CleanTokenAttribute> tokSeq = tokenizer.tokenize(tweet);
      for (CleanTokenAttribute tok : tokSeq) {
        	System.out.println(String.format("%s", tok.getCleanToken().getToken()));
      }
      System.out.println("");
    }
  }
}
