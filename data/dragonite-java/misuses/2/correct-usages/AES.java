import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;

public class ConstructRandomizedIV{
	public void pattern(int offset, int len) {
		SecureRandom random = SecureRandom();
		IVParameterSpec iv = new IvParameterSpec(random);
	}
}
