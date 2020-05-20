import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;

public class ConstructIvParameterSpec {
	public void pattern() {
		SecureRandom iv = new SecureRandom(); 
		byte bytes[] = new byte[100];
		iv.nextBytes(bytes);
		IvParameterSpec ips = new IvParameterSpec(bytes);
	}
}
