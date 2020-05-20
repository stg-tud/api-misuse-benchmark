import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.NoSuchPaddingException;

public class ConstructMessageDigest{
	public void pattern() throws NoSuchAlgorithmException, NosuchPaddingException{
		MessageDigest md = MessageDigest.getInstance("SHA-512");
	}
}
