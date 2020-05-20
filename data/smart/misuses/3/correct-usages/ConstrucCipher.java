import javax.crypto.Cipher;
import java.security.SecureRandom;
import java.security.NoSuchAlgorithmException;
import java.security.InvalidKeyException;

public class ConstrucCipher {
	public void pattern(java.security.Key key) throws Exception {
	        Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
		SecureRandom random = new SecureRandom();
		c.init(Cipher.ENCRYPT_MODE, key, random); 	
	}
}
