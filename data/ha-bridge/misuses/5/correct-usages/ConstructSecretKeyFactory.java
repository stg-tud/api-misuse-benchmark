import javax.crypto.SecretKeyFactory;
import java.security.NoSuchAlgorithmException;

public class ConstructSecretKeyFactory{
	public void pattern() throws NoSuchAlgorithmException {
		SecretKeyFactory skf = SecretKeyFactory.getInstance("PBEWithHmacSHA512AndAES_128");
	}

}
