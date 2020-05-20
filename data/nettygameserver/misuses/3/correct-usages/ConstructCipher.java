import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public class ConstructCipher {
	public void pattern() throws NoSuchAlgorithmException, NoSuchPaddingException {
	      Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
	}
}
