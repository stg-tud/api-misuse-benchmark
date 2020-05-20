import javax.crypto.Cipher;
import javax.crypto.NoSuchPaddingException;
import java.security.NoSuchAlgorithmException;

public class ConstructCipher {
	public void pattern() throws NoSuchPaddingException, NoSuchAlgorithmException {
		Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
	}
}
