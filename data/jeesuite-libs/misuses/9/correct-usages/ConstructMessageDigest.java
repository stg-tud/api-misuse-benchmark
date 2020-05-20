import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class ConstructMessageDigest{
	public void pattern() throws NoSuchAlgorithmException {
		MessageDigest md = MessageDigest.getInstance("SHA-512");
	}
}
