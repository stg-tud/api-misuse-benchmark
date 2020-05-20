import javax.crypto.Cipher;
import java.security.NoSuchAlgorithmException;

public class ConstructCipher {
	public void pattern()  throws Exception{
		Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
	}
}
