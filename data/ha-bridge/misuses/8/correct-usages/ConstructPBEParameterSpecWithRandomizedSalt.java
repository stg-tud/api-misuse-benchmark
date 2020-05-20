import javax.crypto.spec.PBEParameterSpec;
import java.security.SecureRandom;


public class ConstructPBEParameterSpecWithRandomizedSalt{
       public void pattern(int iterationCount)  {
		SecureRandom salt = new SecureRandom();
		byte bytes[] = new byte[100];
		salt.nextBytes(bytes);
		PBEParameterSpec pbkps = new PBEParameterSpec(bytes, iterationCount);
       }
}
