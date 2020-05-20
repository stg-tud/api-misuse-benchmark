import javax.crypto.spec.SecretKeySpec;
import javax.crypto.SecretKeyFactory;
import javax.crypto.SecretKey;
import javax.crypto.spec.PBEKeySpec;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;

public class ConstructSecretKeySpec {
	public void pattern(char[] password,byte[] salt,int iterationCount,int keylength,java.lang.String algorithm)  throws NoSuchAlgorithmException, InvalidKeySpecException{
		SecretKeyFactory skf = SecretKeyFactory.getInstance("PBEWithHmacSHA512AndAES_128");
		PBEKeySpec pbeks = new PBEKeySpec(password, salt, iterationCount, keylength);
		SecretKey key =  skf.generateSecret(pbeks);
		byte keyMaterial[] = key.getEncoded();
		SecretKeySpec sks = new SecretKeySpec(keyMaterial, algorithm);
	}
}

