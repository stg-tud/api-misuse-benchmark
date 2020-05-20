import javax.crypto.spec.PBEKeySpec;

public class ConstructPBEKeySpec{
	public void pattern(char[] password,byte[] salt, int iterationCount, int keylength){
		PBEKeySpec pbeks = new PBEKeySpec(password, salt, iterationCount, keylength);
	}
}
