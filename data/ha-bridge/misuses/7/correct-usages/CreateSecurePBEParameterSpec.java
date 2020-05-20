import javax.crypto.spec.PBEParameterSpec;


public class CreateSecurePBEParameterSpec {
 	public void pattern(byte[] salt) {
		PBEParameterSpec pbeps = new PBEParameterSpec(salt, 15000);
	}
}
