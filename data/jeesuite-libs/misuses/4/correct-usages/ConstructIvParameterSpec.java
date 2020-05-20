import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;
import java.security.NoSuchAlgorithmException;

public class ConstructIvParameterSpec {
	public void pattern() throws NoSuchAlgorithmException{
		SecureRandom iv = new SecureRandom(); 
		byte bytes[] = new byte[100];
		iv.nextBytes(bytes);
		IvParameterSpec ips = new IvParameterSpec(bytes);
	}
}
