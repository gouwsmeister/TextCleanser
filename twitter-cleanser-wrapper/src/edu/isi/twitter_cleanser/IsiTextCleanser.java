// =================================================================================================
// Copyright 2011 Stephan Gouws
// -------------------------------------------------------------------------------------------------
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this work except in compliance with the License.
// You may obtain a copy of the License in the LICENSE file, or at:
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =================================================================================================

package edu.isi.twitter_cleanser;

import java.util.ArrayList;
import java.util.List;

import com.google.common.base.Preconditions;
import com.twitter.common.text.filter.PunctuationFilter;
import com.twitter.common.text.token.TokenStream;
import com.twitter.common.text.token.TokenizedCharSequence;
import com.twitter.common.text.token.TokenizedCharSequenceStream;
import com.twitter.common.text.tokenizer.LatinTokenizer;

/**
 * Default implementation of a Text Cleanser for normalising tweets to their most likely standard form. 
 * For sample usage, please consult annotated code example in {@link TextCleanserUsageExample}.
 */
public class IsiTextCleanser {
  private TokenStream tokenizationStream = new CleansedTokenStream();

  // use Builder.
  private IsiTextCleanser() { }

  /**
   * Returns {@code TokenStream} to tokenize a text.
   *
   * @return TokenStream to tokenize the text
   */
  public TokenStream getDefaultTokenStream() {
    return tokenizationStream;
  }

  /**
   * Tokenizes a CharSequence, and returns a list of {@code CleanTokenAttribute}s as a result.
   *
   * @param input text to be tokenized
   * @return a TokenizedCharSequence instance
   */
public List<CleanTokenAttribute> tokenize(CharSequence input) {
	Preconditions.checkNotNull(input);
	TokenStream stream = this.getDefaultTokenStream();
	List<CleanTokenAttribute> result = new ArrayList<CleanTokenAttribute>();
	stream.reset(input);
	while(stream.incrementToken()) {
		CleanTokenAttribute ctAttribute = (CleanTokenAttribute)stream.getAttribute(CleanTokenAttribute.class).clone();
		result.add(ctAttribute);
	}
	return result;
}

  /**
   * Tokenizes a CharSequence into a list of Strings.
   *
   * @param input text to be tokenized
   * @return a list of tokens as String objects
   */
  public List<String> tokenizeToStrings(CharSequence input) {
    Preconditions.checkNotNull(input);
    TokenStream tokenizer = getDefaultTokenStream();
    tokenizer.reset(input);
    return tokenizer.toStringList();
  }

  /**
   * Builder for {@link DefaultTwitterTextTokenizer}
   */
  public static final class Builder {
    private final IsiTextCleanser tokenizer = new IsiTextCleanser();

    private boolean keepPunctuation = true;

    /**
     * Sets true to keep punctuations in the output of the tokenization.
     *
     * @param keepPunctuation true to keep punctuations.
     * @return this Builder
     */
    public Builder setKeepPunctuation(boolean keepPunctuation) {
      this.keepPunctuation = keepPunctuation;
      return this;
    }

    public IsiTextCleanser build() {
      if (!keepPunctuation) {
        tokenizer.tokenizationStream =
            new PunctuationFilter(tokenizer.tokenizationStream);
      }

      return tokenizer;
    }
  }
}
