import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.security.SecureRandom;
import java.security.NoSuchAlgorithmException;

public class ConstructCipher {
	public void pattern(SecureRandom random) throws Exception {
		KeyGenerator kg = KeyGenerator.getInstance("AES128"); 
		SecretKey key = kg.generateKey();
	        Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
		c.init(Cipher.ENCRYPT_MODE, key, random); 	
	}
}
